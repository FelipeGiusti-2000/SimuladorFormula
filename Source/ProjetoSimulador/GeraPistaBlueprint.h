// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Engine/DataTable.h"
#include "GeraPistaBlueprint.generated.h"




/**
 * 
 */
UCLASS()
class PROJETOSIMULADOR_API UGeraPistaBlueprint : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "General Parameters")
		static void geradDado();
	
};


USTRUCT(BlueprintType)
struct FPlayerAttackMontage : public FTableRowBase
{
	GENERATED_BODY()
public:
	/** montage **/
	UPROPERTY(EditAnywhere, BlueprintReadWrite)
		float x;
	/** count of animations in montage **/
	UPROPERTY(EditAnywhere, BlueprintReadWrite)
		float y;
	/** description **/
	UPROPERTY(EditAnywhere, BlueprintReadWrite)
		float z;
};


